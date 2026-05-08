def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos(p, d=(0, 0)):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict) and "x" in p and "y" in p:
            return int(p["x"]), int(p["y"])
        return d

    sx, sy = pos(observation.get("self_position", [0, 0]))
    ox, oy = pos(observation.get("opponent_position", [0, 0]))
    self_role = observation.get("self_role", "pursuer")

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = o[0], o[1]
        elif isinstance(o, dict) and "x" in o and "y" in o:
            x, y = o["x"], o["y"]
        else:
            continue
        try:
            x, y = int(x), int(y)
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        if self_role == "evader":
            val = dist
            if best is None or val > best_val:
                best, best_val = (dx, dy), val
            elif val == best_val and (dx, dy) < best:
                best = (dx, dy)
        else:
            val = -dist
            if best is None or val > best_val:
                best, best_val = (dx, dy), val
            elif val == best_val and (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]