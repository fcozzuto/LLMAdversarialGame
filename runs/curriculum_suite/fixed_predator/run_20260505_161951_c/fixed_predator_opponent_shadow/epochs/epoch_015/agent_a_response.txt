def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        best = max(legal, key=lambda m: (man(m[2], m[3], ox, oy), m[0] == 0 and m[1] == 0))
        return [best[0], best[1]]

    best_move = None
    best_val = -10**18

    for dx, dy, nx, ny in legal:
        best_race = -10**18
        best_rd = 10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            race = od - sd  # positive => we are closer than opponent by that margin
            if race > best_race or (race == best_race and sd < best_rd):
                best_race = race
                best_rd = sd
        # Value: secure biggest race; if tied, prefer faster pickup; slight penalty for moving closer to opponent
        opp_d = man(nx, ny, ox, oy)
        val = best_race * 100 - best_rd - (80 - opp_d) // 10
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]