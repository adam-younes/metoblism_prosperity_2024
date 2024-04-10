from datamodel import OrderDepth, UserId, TradingState, Order
# import pandas
# import numpy
# import statistics
# import math
import typing
import collections
# import jasonpickle
import copy


class Trader:

    position_limit = {
        'AMETHYSTS': 20,
        'STARFRUIT': 20
    }

    position = {
        'AMETHYSTS': 0,
        'STARFRUIT': 0 
    }

    def unpack_orders(self, orders, intent=-1):
        volume = 0
        best_bid_ask = -1
        max_volume = -1

        for ask, vol in orders:
            volume += vol
            if volume > max_volume:
                max_volume = volume
                best_value = ask

        return volume, best_bid_ask

    def trade_amethysts(self, order_depth, max_bid, min_ask):
        AME = 'AMETHYSTS'
        orders: List[Order] = []
        current_position = self.position[AME]

        for current_ask, current_ask_amount in order_depth.sell_orders.items():
            if current_ask <= max_bid and current_position < self.position_limit[AME]:
                orders.append(Order(AME, current_ask, -current_ask_amount))

        for current_bid, current_bid_amount in order_depth.buy_orders.items():
            if current_bid >= min_ask and current_position > -self.position_limit[AME]:
                orders.append(Order(AME, current_bid, -current_bid_amount))

        return orders


    def trade_starfruit(self, order_depth, max_bid, min_ask):
        STA = 'STARFRUIT'
        # buy at lowball price every morning
        # sell at highball every afternoon
        orders: List[Order] = []
        
        sell_orders = order_depth.sell_orders.items()
        buy_orders = order_depth.buy_orders.items()

        sell_volume, best_ask = self.unpack_orders(sell_orders)
        buy_volume, best_bid = self.unpack_orders(buy_orders)

        current_position = self.position[STA]

        for ask, vol in sell_orders:
            

        return

    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all 
        # symbols as an input, and outputs a list of orders to be sent
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        # for key, val in state.position.items():
        #    self.cur_equity[key] = val
        
        all_orders = { 'AMETHYSTS': [],
                       'STARFRUIT': [] }

        all_orders['AMETHYSTS'] = self.trade_amethysts(state.order_depths['AMETHYSTS'], 10000, 10000)

        # as TradingState.traderData on next execution.
        traderData = "SAMPLE" 

        conversions = 1
        return all_orders, conversions, traderData
