def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            obs_set.add((int(a["x"]), int(a["y"])))
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            obs_set.add((int(a[0]), int(a[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None  # tuple

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue

        our_d = None
        opp_d = None
        for rx, ry in resources:
            d = dist(nx, ny, rx, ry)
            if our_d is None or d < our_d or (d == our_d and (rx, ry) < (rx_best, ry_best)):
                our_d = d
                rx_best, ry_best = rx, ry
        opp_d = dist(ox, oy, rx_best, ry_best)

        # Prefer moves that keep opponent farther than us, then bring us closer
        val = (opp_d - our_d, -our_d, -dist(nx, ny, ox, oy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]