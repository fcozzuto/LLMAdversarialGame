def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_goal():
        if not unclaimed:
            return None
        best = None
        bd = None
        for x, y in unclaimed:
            d = abs(x - sx) + abs(y - sy)
            if bd is None or d < bd or (d == bd and (x, y) < best):
                bd = d
                best = (x, y)
        return best

    goal = best_goal()

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if goal is None:
            # Keep distance from opponent; deterministic tie-break by (dx,dy).
            s = (abs(nx - ox) + abs(ny - oy), 0)
        else:
            d_goal = abs(goal[0] - nx) + abs(goal[1] - ny)
            d_opp = abs(ox - nx) + abs(oy - ny)
            s = (-d_goal, d_opp)  # prefer smaller d_goal, larger d_opp
        if best_score is None or s > best_score or (s == best_score and (dx, dy) < best_move):
            best_score = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]