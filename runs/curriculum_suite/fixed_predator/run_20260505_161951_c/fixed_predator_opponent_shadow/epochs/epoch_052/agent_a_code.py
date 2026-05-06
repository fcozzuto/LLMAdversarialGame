def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obs = set(tuple(p) for p in observation.get("obstacles", []) or [])
    res = [tuple(p) for p in observation.get("resources", []) or []]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best_move = moves[0][:2]
    best_val = None
    if res:
        for dx, dy, nx, ny in moves:
            # Prefer closer to resources than opponent, and farther from opponent if can't contest.
            best_gain = -10**9
            min_my = 10**9
            min_opp = 10**9
            for rx, ry in res:
                d_my = man(nx, ny, rx, ry)
                d_opp = man(ox, oy, rx, ry)
                if d_my < min_my:
                    min_my = d_my
                if d_opp < min_opp:
                    min_opp = d_opp
                # Contest score: bigger is better; tie-break with closeness.
                gain = (d_opp - d_my) * 1000 - d_my
                if gain > best_gain:
                    best_gain = gain
            # Also incorporate safety relative to opponent.
            opp_dist = man(nx, ny, ox, oy)
            v = (best_gain, -min_my, opp_dist)
            if best_val is None or v > best_val:
                best_val = v
                best_move = (dx, dy)
    else:
        # No resources: move away from opponent deterministically, prioritizing valid moves.
        for dx, dy, nx, ny in moves:
            v = (man(nx, ny, ox, oy), -abs((nx - sx)) - abs((ny - sy)))
            if best_val is None or v > best_val:
                best_val = v
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]