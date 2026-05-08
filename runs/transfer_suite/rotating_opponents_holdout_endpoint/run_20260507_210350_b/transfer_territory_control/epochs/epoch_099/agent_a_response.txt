def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for o in observation.get("obstacles") or []:
        try:
            x, y = o
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    self_cells = set()
    for p in observation.get("self_territory") or []:
        try:
            x, y = p
            x, y = int(x), int(y)
            if inb(x, y):
                self_cells.add((x, y))
        except Exception:
            pass

    opp_cells = set()
    for p in observation.get("opponent_territory") or []:
        try:
            x, y = p
            x, y = int(x), int(y)
            if inb(x, y):
                opp_cells.add((x, y))
        except Exception:
            pass

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        try:
            x, y = p
            x, y = int(x), int(y)
            if inb(x, y):
                unclaimed.add((x, y))
        except Exception:
            pass

    self_cnt = int(observation.get("self_territory_count") or 0)
    opp_cnt = int(observation.get("opponent_territory_count") or 0)
    behind = self_cnt < opp_cnt

    cx, cy = w // 2, h // 2
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)]

    scored = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            scored.append(((-10**9), dx, dy))
            continue

        if (nx, ny) in unclaimed:
            gain = 2
        elif (nx, ny) in self_cells:
            gain = 1
        elif (nx, ny) in opp_cells:
            gain = 3 if behind else 1
        else:
            gain = 0

        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_self = abs(nx - sx) + abs(ny - sy)
        center_bonus = -0.03 * dist_center
        move_penalty = -0.01 * dist_self

        scored.append((gain + center_bonus + move_penalty, dx, dy))

    best = max(scored, key=lambda t: (t[0], -abs(t[1]), -abs(t[2])))
    return [int(best[1]), int(best[2])]