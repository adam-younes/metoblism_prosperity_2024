from datamodel import OrderDepth, UserId, TradingState, Order
# import pandas
import numpy as np
# import statistics
# import math
import typing
import collections
# import jasonpickle
import copy

INF = 10e9

class Trader:

    position_limit = {
        'AMETHYSTS': 20,
        'STARFRUIT': 20
    }

    position = {
        'AMETHYSTS': 0,
        'STARFRUIT': 0 
    }

    product_cache = {
        'AMETHYSTS': np.array([]),
        'STARFRUIT': np.array([])
    }

    starfruit_count = 100

    def unpack_orders(self, order_dict, buy=0):
        volume = 0
        best_bid_ask = -1
        max_volume = -1

        for ask, vol in order_dict:
            if buy == 0:
                vol *= -1
            volume += vol
            if volume > max_volume:
                max_volume = vol
                best_bid_ask = ask

        return volume, best_bid_ask

    def trade_amethysts(self, order_depth, max_bid, min_ask):
        AME = 'AMETHYSTS'
        orders: List[Order] = []
        current_position = self.position[AME]

        for current_ask, current_ask_amount in order_depth.sell_orders.items():
            if current_ask <= max_bid and current_position < self.position_limit[AME]:
                orders.append(Order(AME, current_ask, -current_ask_amount))
                current_position -= current_ask_amount

        for current_bid, current_bid_amount in order_depth.buy_orders.items():
            if current_bid >= min_ask and current_position > -self.position_limit[AME]:
                orders.append(Order(AME, current_bid, -current_bid_amount))
                current_position -= current_bid_amount

        return orders

    def linear_regression(self, product):
        A = np.vstack([np.ones(len(product)), np.arange(1, len(product) + 1)]).T
        y = product[:, np.newaxis]

        alpha = np.dot(np.dot(np.linalg.inv(np.dot(A.T, A)), A.T), y)

        # Predicting the value for a given x
        prediction = alpha[0] + alpha[1] * (len(product) + 1)

        return prediction

    def trade_starfruit(self, order_depth, max_bid, min_ask):
        STA = 'STARFRUIT'
        # buy at lowball price every morning
        # sell at highball every afternoon

        orders: List[Order] = []

        current_position = self.position[STA]

        sell_orders = order_depth.sell_orders.items()
        buy_orders = order_depth.sell_orders.items()

        for current_ask, current_ask_amount in sell_orders:
            if current_ask <= max_bid and current_position < self.position_limit[STA]:
                orders.append(Order(STA, current_ask, -current_ask_amount))
                current_position -= current_ask_amount

        for current_bid, current_bid_amount in sell_orders:
            orders.append(Order(STA, current_bid, -current_bid_amount))
            if current_bid >= min_ask and current_position > -self.position_limit[STA]:
                orders.append(Order(STA, current_ask, -current_ask_amount))
                current_position -= current_bid_amount

       # sell_volume, best_ask = self.unpack_orders(sell_orders)
       # buy_volume, best_bid = self.unpack_orders(buy_orders)

       # better_ask = best_ask - 1
       # better_bid = best_bid + 1

       # final_bid = min(max_bid, better_bid)
       # final_ask = max(min_ask, better_ask)

       # for current_ask, current_ask_amount in sell_orders:
       #     if current_ask <= max_bid or (self.position[STA] < 0 and current_ask == max_bid + 1) and current_position < self.position_limit[STA]:
       #         order_volume = min(-current_ask_amount, self.position_limit[STA] - current_position)
       #         current_position += order_volume
       #         orders.append(Order(STA, current_ask, order_volume))

       # if current_position < self.position_limit[STA]:
       #     volume = self.position_limit[STA] - current_position
       #     orders.append(Order(STA, final_bid, volume))
       #     current_position += volume

       # current_position = self.position_limit[STA]

       # for current_bid, current_bid_amount in buy_orders:
       #     if current_ask >= min_ask or (self.position[STA] > 0 and current_bid == min_ask + 1) and current_position > -self.position_limit[STA]:
       #         order_volume = max(-current_bid_amount, -self.position_limit[STA] - current_position)
       #         current_position += order_volume
       #         orders.append(Order(STA, current_bid, order_volume))

       # if current_position > -self.position_limit[STA]:
       #     volume = -self.position_limit[STA] - current_position
       #     orders.append(Order(STA, final_ask, volume))
       #     current_position += volume

        return orders

    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all 
        # symbols as an input, and outputs a list of orders to be sent

        # for key, val in state.position.items():
        #    self.cur_equity[key] = val
        
        all_orders = { 'AMETHYSTS': [],
                       'STARFRUIT': [] }

        order_depths = state.order_depths

        all_orders['AMETHYSTS'] += self.trade_amethysts(order_depths['AMETHYSTS'], 10000, 10000)

        if len(self.product_cache['STARFRUIT']) == self.starfruit_count:
            np.delete(self.product_cache['STARFRUIT'], 0)
                
        _, best_sta_bid = self.unpack_orders(order_depths['STARFRUIT'].buy_orders.items(), 1)
        _, best_sta_ask = self.unpack_orders(order_depths['STARFRUIT'].sell_orders.items())

        self.product_cache['STARFRUIT'] = np.append(self.product_cache['STARFRUIT'], [(best_sta_bid + best_sta_ask) / 2])

        if len(self.product_cache['STARFRUIT']) >= self.starfruit_count:
            starfruit_next = self.linear_regression(self.product_cache['STARFRUIT'])
            # print("PREDICTION: " + str(starfruit_next))
            # print("BUY_ORDERS: " + str(order_depths['STARFRUIT'].buy_orders))
            # print("SELL_ORDERS: " + str(order_depths['STARFRUIT'].sell_orders))
            all_orders['STARFRUIT'] += self.trade_starfruit(order_depths['STARFRUIT'], starfruit_next, starfruit_next)

        # as TradingState.traderData on next execution.
        traderData = "SAMPLE"

        conversions = 1
        return all_orders, conversions, traderData
