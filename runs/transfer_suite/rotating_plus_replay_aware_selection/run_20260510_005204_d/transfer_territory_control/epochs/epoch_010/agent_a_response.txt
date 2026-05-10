def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = opp_pos[0], opp_pos[1]

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    un_set = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))
    self_set = set(tuple(p) for p in (observation.get("self_territory", []) or []))

    self_tc = int(observation.get("self_territory_count", 0))
    opp_tc = int(observation.get("opponent_territory_count", 0))
    leader_bonus = 0.75 if (int(observation.get("turn_index", 0)) % 10 == 0 and self_tc >= opp_tc) else 0.0

    best = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_set:
            val = 18.0 + leader_bonus
            val -= 0.5 * dist(nx, ny, ox, oy)
            val += 0.4 * dist(sx, sy, ox, oy)
        elif (nx, ny) in un_set:
            myd = dist(nx, ny, ox, oy)
            my2 = dist(nx, ny, sx, sy)
            oppd = dist(nx, ny, ox, oy)
            val = 9.0 + leader_bonus
            val -= 0.35 * myd
            val -= 0.08 * my2
            val += 2.0 if oppd > myd else 0.0
        elif (nx, ny) in self_set:
            val = 3.0
            val += 0.2 * dist(nx, ny, ox, oy)
            val += 0.1 * (leader_bonus * 2.0)
        else:
            val = 1.0
            val += 0.08 * dist(nx, ny, ox, oy)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]