def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_t = None
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        deny = (od - sd) * 8 - sd
        center_bias = -(((rx - cx0) ** 2 + (ry - cy0) ** 2) * 1e-4)
        key = (deny + center_bias, -od, -sd, rx, ry)
        if best_t is None or key > best_t[0]:
            best_t = (key, rx, ry)
    tx, ty = best_t[1], best_t[2]

    best_move = (-(10**9), 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            sd_after = man(nx, ny, tx, ty)
            od_after = man(ox, oy, tx, ty)  # opponent static for eval
            # Prefer moving closer to our target, but also "deny" by keeping opponent farther.
            deny_after = (od_after - sd_after)
            # Slightly prefer moves that increase distance from opponent to avoid being lapped.
            opp_dist = man(nx, ny, ox, oy)
            # Multi-criteria deterministic tie-breakers toward resources vicinity.
            move_key = (deny_after * 10 - sd_after, opp_dist, -sd_after, -abs(nx - tx) - abs(ny - ty), dx, dy)
            if move_key > best_move[0:]:
                best_move = (move_key[0], dx, dy)
    return [int(best_move[1]), int(best_move[2])]