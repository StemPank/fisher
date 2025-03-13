
import core.agent.table_for_agent as table_for_agent
import numpy as np

def calculation_of_results(name, iteration_value, commission, initial_balance = 10000, leverage=1):
    order_data = table_for_agent.get_data_trade_table(name)

    order_groups = {}
    # Группируем сделки по identifier
    for identifier, timestamp, price, quantity, side in order_data:
        if identifier not in order_groups:
            order_groups[identifier] = []
        order_groups[identifier].append((timestamp, price, quantity, side))
    
    total_transactions=[]
    equity_curve = [initial_balance]
    trade_durations = []  # Список длительностей сделок
    for identifier, trades in order_groups.items():
        segment = []  # Текущий набор точек для соединения
        last_side = None
        current_quantity = 0  # Общий объем открытых позиций
        avg_entry_price = 0  # Средняя цена входа

        for timestamp, price, quantity, side in trades:
            if not segment:
                segment.append((timestamp, price, quantity, side))
                current_quantity += quantity if side == "BUY" else -quantity
                avg_entry_price = price  # Начальная цена входа
            else:
                # Продолжаем соединять, если направление одинаковое (SELL → SELL или BUY → BUY)
                if last_side == side:
                    # Пересчитываем среднюю цену входа
                    total_cost = avg_entry_price * abs(current_quantity) + price * quantity
                    current_quantity += quantity if side == "BUY" else -quantity
                    avg_entry_price = total_cost / abs(current_quantity)
                    segment.append((timestamp, price, quantity, side))
                else:
                    current_quantity += quantity if side == "BUY" else -quantity
                    segment.append((timestamp, price, quantity, side))
                    if current_quantity == 0:
                        total_transactions.append((segment, avg_entry_price))
                        trade_durations.append(segment[-1][0] - segment[0][0])  # Добавляем длительность сделки
                        segment = []  # Начинаем новый сегмент
                        current_quantity = 0
                        avg_entry_price = 0
            last_side = side
    
    purchase_transaction=[]
    sales_transaction=[]

    profitable_trades = 0
    unprofitable_trades = 0
    total_profit = 0

    total_profit = 0
    total_loss = 0
    total_trades = len(total_transactions)

    trade_profits = []  # Для расчета средней прибыли

    for trades, avg_entry_price in total_transactions:
        open_trade = trades[0]
        close_trade = trades[-1]
        open_price = open_trade[1]
        close_price = close_trade[1]
        volume = sum(q for _, _, q, _ in trades)  # Считаем общий объем сделки

        # **Расчет прибыли с учетом средней цены входа**
        trade_profit = 0
        if open_trade[3] == "BUY":  # Покупка → Продажа
            trade_profit = (close_price - avg_entry_price) * volume
        else:  # Продажа → Покупка
            trade_profit = (avg_entry_price - close_price) * volume

        # **Вычитаем комиссию (2 раза — на вход и выход)**
        trade_profit -= (avg_entry_price * volume * commission)  
        trade_profit -= (close_price * volume * commission)


        if trade_profit > 0:
            total_profit += trade_profit
            profitable_trades += 1
        else:
            total_loss += abs(trade_profit)
            unprofitable_trades += 1

        trade_profits.append(trade_profit)
        equity_curve.append(equity_curve[-1] + trade_profit)

        if open_trade[3] == "BUY":
            purchase_transaction.append((trades, avg_entry_price))
        else:
            sales_transaction.append((trades, avg_entry_price))

    # **Чистая прибыль**
    net_profit = total_profit - total_loss

    # **Средняя прибыль на сделку**
    avg_profit_per_trade = net_profit / total_trades if total_trades > 0 else 0

    # **Win Rate (Процент прибыльных сделок)**
    win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0

    # **Profit Factor (Фактор прибыли)**
    profit_factor = (total_profit / total_loss) if total_loss > 0 else float('inf')

    # **Expectancy (Ожидаемая доходность сделки)**
    avg_win = total_profit / profitable_trades if profitable_trades > 0 else 0
    avg_loss = total_loss / unprofitable_trades if unprofitable_trades > 0 else 0
    loss_rate = 100 - win_rate
    expectancy = (avg_win * (win_rate / 100)) - (avg_loss * (loss_rate / 100))

    max_drawdown = max([max(equity_curve[:i+1]) - equity_curve[i] for i in range(1, len(equity_curve))]) if len(equity_curve) > 1 else 0
    recovery_factor = net_profit / max_drawdown if max_drawdown > 0 else float('inf')
    std_dev = np.std(trade_profits) if trade_profits else 0
    sharpe_ratio = (np.mean(trade_profits) / std_dev) if std_dev > 0 else float('inf')
    calmar_ratio = (net_profit / max_drawdown) if max_drawdown > 0 else float('inf')
    roi = (net_profit / initial_balance) * 100 if initial_balance > 0 else 0
    roe = (net_profit / (initial_balance * leverage)) * 100 if initial_balance > 0 and leverage > 0 else 0

    avg_trade_duration = np.mean(trade_durations) if trade_durations else 0  # Средняя длительность сделки

    (buy_profitable_trades, buy_unprofitable_trades, buy_total_profit, buy_total_loss, buy_net_profit, 
    buy_avg_profit_per_trade, buy_win_rate, buy_profit_factor, buy_expectancy, buy_max_drawdown, buy_recovery_factor, 
    buy_sharpe_ratio, buy_calmar_ratio, buy_roi, buy_roe, buy_std_dev, buy_avg_trade_duration) = calculation_of_results_buy(purchase_transaction, iteration_value, commission, equity_curve, leverage=1)

    (sell_profitable_trades, sell_unprofitable_trades, sell_total_profit, sell_total_loss, sell_net_profit, 
    sell_avg_profit_per_trade, sell_win_rate, sell_profit_factor, sell_expectancy, sell_max_drawdown, sell_recovery_factor, 
    sell_sharpe_ratio, sell_calmar_ratio, sell_roi, sell_roe, sell_std_dev, sell_avg_trade_duration) = calculation_of_results_buy(sales_transaction , iteration_value, commission, equity_curve, leverage=1)

    lenpurchase_transaction=len(purchase_transaction)
    lensales_transaction = len(sales_transaction)
    data_for_table = (iteration_value, total_trades, profitable_trades, unprofitable_trades, total_profit, total_loss, net_profit, 
            avg_profit_per_trade, win_rate, profit_factor, expectancy, max_drawdown, recovery_factor, 
            sharpe_ratio, calmar_ratio, roi, roe, std_dev, avg_trade_duration, lenpurchase_transaction, buy_profitable_trades, buy_unprofitable_trades, buy_total_profit, buy_total_loss, buy_net_profit, 
            buy_avg_profit_per_trade, buy_win_rate, buy_profit_factor, buy_expectancy, buy_max_drawdown, buy_recovery_factor, 
            buy_sharpe_ratio, buy_calmar_ratio, buy_roi, buy_roe, buy_std_dev, buy_avg_trade_duration, lensales_transaction, sell_profitable_trades, sell_unprofitable_trades, sell_total_profit, sell_total_loss, sell_net_profit, 
            sell_avg_profit_per_trade, sell_win_rate, sell_profit_factor, sell_expectancy, sell_max_drawdown, sell_recovery_factor, 
            sell_sharpe_ratio, sell_calmar_ratio, sell_roi, sell_roe, sell_std_dev, sell_avg_trade_duration)
    record_to_table = table_for_agent.insert_data_to_results_table(name, data_for_table)
    # print(f"Текущий баланс: {equity_curve[-1]:.2f}")
    # print(equity_curve)
    # print(f"Всего сделок {len(total_transactions)}")
    # print(f"Прибыльных сделок {profitable_trades}")
    # print(f"Убыточных сделок {unprofitable_trades}")
    # print(f"Общая прибыль (Total Profit): {total_profit:.2f}")
    # print(f"Общий убыток (Total Loss): {total_loss:.2f}")
    # print(f"Чистая прибыль (Net Profit): {net_profit:.2f}")
    # print(f"Средняя прибыль на сделку (Average Profit per Trade): {avg_profit_per_trade:.2f}")
    # print(f"Процент прибыльных сделок (Win Rate): {win_rate:.2f}")
    # print(f"Фактор прибыли (Profit Factor): {profit_factor:.2f} Значение > 1 показывает, что стратегия прибыльная.")
    # print(f"Ожидаемая доходность сделки (Expectancy): {expectancy:.2f} Если Expectancy > 0, значит стратегия прибыльная на длинной дистанции.")
    # print(f"Максимальная просадка (Maximum Drawdown): {max_drawdown:.2f} Самый большой спад от пика депозита до минимума. Выражается в % и показывает, насколько опасна стратегия")
    # print(f"Коэффициент восстановления (Recovery Factor): {recovery_factor:.2f} Чем выше, тем быстрее стратегия восстанавливает убытки." )
    # print(f"Коэффициент Шарпа (Sharpe Ratio) Чем выше, тем лучше: {sharpe_ratio:.2f}")
    # print(f"Коэффициент Калмара (Calmar Ratio) Помогает оценить, насколько стратегия устойчива к рискам.: {calmar_ratio:.2f}")
    # print(f"ROI (Return on Investment, Доходность на капитал): {roi:.2f}%")
    # print(f"ROE (с учетом плеча {leverage}x): {roe:.2f}%")
    # print(f"Стандартное отклонение доходности (Standard Deviation): {std_dev:.2f} показывает волатильность доходов")
    # print(f"Средняя длительность сделки: {avg_trade_duration:.2f} секунд \n")

def calculation_of_results_buy(purchase_transaction, iteration_value, commission, equity_curve, initial_balance = 10000, leverage=1):

    total_transactions=purchase_transaction
    equity_curve = equity_curve
    trade_durations = [segment[-1][0]-segment[0][0] for segment, _ in total_transactions if len(total_transactions)>1]  # Список длительностей сделок
    
    profitable_trades = 0
    unprofitable_trades = 0
    total_profit = 0

    total_profit = 0
    total_loss = 0
    total_trades = len(total_transactions)

    trade_profits = []  # Для расчета средней прибыли

    for trades, avg_entry_price in total_transactions:
        open_trade = trades[0]
        close_trade = trades[-1]
        # open_price = open_trade[1]
        close_price = close_trade[1]
        volume = sum(q for _, _, q, _ in trades)  # Считаем общий объем сделки

        # **Расчет прибыли с учетом средней цены входа**
        trade_profit = 0
        if open_trade[3] == "BUY":  # Покупка → Продажа
            trade_profit = (close_price - avg_entry_price) * volume
        else:  # Продажа → Покупка
            trade_profit = (avg_entry_price - close_price) * volume

        # **Вычитаем комиссию (2 раза — на вход и выход)**
        trade_profit -= (avg_entry_price * volume * commission)  
        trade_profit -= (close_price * volume * commission)


        if trade_profit > 0:
            total_profit += trade_profit
            profitable_trades += 1
        else:
            total_loss += abs(trade_profit)
            unprofitable_trades += 1

        trade_profits.append(trade_profit)
        equity_curve.append(equity_curve[-1] + trade_profit)

    # **Чистая прибыль**
    net_profit = total_profit - total_loss

    # **Средняя прибыль на сделку**
    avg_profit_per_trade = net_profit / total_trades if total_trades > 0 else 0

    # **Win Rate (Процент прибыльных сделок)**
    win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0

    # **Profit Factor (Фактор прибыли)**
    profit_factor = (total_profit / total_loss) if total_loss > 0 else float('inf')

    # **Expectancy (Ожидаемая доходность сделки)**
    avg_win = total_profit / profitable_trades if profitable_trades > 0 else 0
    avg_loss = total_loss / unprofitable_trades if unprofitable_trades > 0 else 0
    loss_rate = 100 - win_rate
    expectancy = (avg_win * (win_rate / 100)) - (avg_loss * (loss_rate / 100))

    max_drawdown = max([max(equity_curve[:i+1]) - equity_curve[i] for i in range(1, len(equity_curve))]) if len(equity_curve) > 1 else 0
    recovery_factor = net_profit / max_drawdown if max_drawdown > 0 else float('inf')
    std_dev = np.std(trade_profits) if trade_profits else 0
    sharpe_ratio = (np.mean(trade_profits) / std_dev) if std_dev > 0 else float('inf')
    calmar_ratio = (net_profit / max_drawdown) if max_drawdown > 0 else float('inf')
    roi = (net_profit / initial_balance) * 100 if initial_balance > 0 else 0
    roe = (net_profit / (initial_balance * leverage)) * 100 if initial_balance > 0 and leverage > 0 else 0

    avg_trade_duration = np.mean(trade_durations) if trade_durations else 0  # Средняя длительность сделки

    return (profitable_trades, unprofitable_trades, total_profit, total_loss, net_profit, 
            avg_profit_per_trade, win_rate, profit_factor, expectancy, max_drawdown, recovery_factor, 
            sharpe_ratio, calmar_ratio, roi, roe, std_dev, avg_trade_duration)


