def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx + dy
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources: return [0, 0]

    opp_row = oy; opp_col = ox
    valid_targets = [(rx, ry) for (rx, ry) in resources if (rx, ry) not in obstacles]
    if not valid_targets: return [0, 0]

    best_move = (0, 0); best_val = -10**9; best_tie = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        # choose the target where we can gain most over opponent, with a sweep-row bonus
        cur_best = -10**9; cur_tie = 10**9
        for rx, ry in valid_targets:
            sd = md(nx, ny, rx, ry); od = md(ox, oy, rx, ry)
            if sd == 0:
                adv = 10**6
            else:
                adv = (od - sd)
            # sweep-row-ish: prefer targets sharing row/col with opponent
            if ry == opp_row: adv += 2
            if rx == opp_col: adv += 2
            # discourage giving opponent immediate pickup
            if md(ox, oy, rx, ry) == 1: adv -= 1
            if adv > cur_best or (adv == cur_best and sd < cur_tie):
                cur_best = adv
                cur_tie = sd
        if cur_best > best_val or (cur_best == best_val and cur_tie < best_tie):
            best_val = cur_best; best_tie = cur_tie; best_move = (dx, dy)

    return [best_move[0], best_move[1]]