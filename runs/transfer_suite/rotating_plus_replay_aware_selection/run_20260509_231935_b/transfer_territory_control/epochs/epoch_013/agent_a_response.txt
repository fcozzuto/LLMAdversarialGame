def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = {tuple(p) for p in (observation.get("obstacles") or [])}
    self_set = {tuple(p) for p in (observation.get("self_territory") or [])}
    opp_set = {tuple(p) for p in (observation.get("opponent_territory") or [])}
    un_set = {tuple(p) for p in (observation.get("unclaimed_cells") or [])}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_to_set(x, y, s):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in s:
                    return True
        return False

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_list = list(opp_set)
    if opp_list:
        op_c = min(opp_list, key=lambda p: md((sx, sy), p))
    else:
        op_c = (w - 1, h - 1)

    un_list = list(un_set)
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = 0.0

        if (nx, ny) in un_set:
            val += 9.0
        if (nx, ny) in opp_set:
            val += 7.0

        if adj_to_set(nx, ny, self_set):
            val += 3.0
        if adj_to_set(nx, ny, opp_set):
            val += 2.0

        if un_list:
            d_un = min(md((nx, ny), t) for t in un_list)
            val += 2.5 / (1 + d_un)
        val += 0.8 / (1 + md((nx, ny), op_c))

        if (dx, dy) == (0, 0):
            val -= 0.05

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]