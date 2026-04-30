def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and r["pos"] is not None and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    deltas.sort(key=lambda t: (t[0] * t[0] + t[1] * t[1], t[0], t[1]))  # deterministic bias toward closer-ish moves

    mx, my = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy

        # Evaluate the best resource after this move, but with opponent-advantage emphasis and separation.
        best_after = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources where we gain on opponent, and avoid getting too close to opponent unless it helps.
            sep = cheb(nx, ny, ox, oy)
            mid = -0.05 * cheb(nx, ny, int(round(mx)), int(round(my)))
            val = (d_op - d_me) + mid + 0.02 * sep
            if val > best_after:
                best_after = val

        # If two moves tie, prefer larger separation and then lexicographic delta.
        sep_cur = cheb(nx, ny, ox, oy)
        tie_key = (best_after, sep_cur, -dx, -dy)
        cur_key = (best_val, -cheb(best_move[0] + sx - sx, best_move[1] + sy - sy, ox, oy) if best_move != (0, 0) else -10**9, 0, 0)
        if best_after > best_val:
            best_val = best_after
            best_move = (dx, dy)
        elif best_after == best_val:
            best_sep = cheb(sx + best_move[0], sy + best_move[1], ox, oy)
            if sep_cur > best_sep or (sep_cur == best_sep and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]