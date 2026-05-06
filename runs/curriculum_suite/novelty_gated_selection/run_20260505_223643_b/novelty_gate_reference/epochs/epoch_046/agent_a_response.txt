def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0] or 0), int(sp[1] or 0)
    ox, oy = int(op[0] or 0), int(op[1] or 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        cx, cy = w // 2, h // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Resource choice: avoid contested items (resource_denier); prefer resources far from opponent
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # After moving, pick the best resource to pursue
        chosen = None
        chosen_val = None
        for rx, ry in resources:
            self_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)

            # Prefer: large opp_d (opponent unlikely to deny soon), then small self_d.
            # Add a slight tie-break toward center to reduce dithering.
            center_bias = abs(rx - (w // 2)) + abs(ry - (h // 2))
            val = (opp_d - self_d, -self_d, -center_bias)

            if chosen_val is None or val > chosen_val:
                chosen_val = val
                chosen = (rx, ry)

        # Also incorporate immediate opponent pressure: don't step closer aggressively unless needed.
        # (resource_denier often harasses; we favor moves that keep or increase distance)
        d_before = dist(sx, sy, ox, oy)
        d_after = dist(nx, ny, ox, oy)
        opp_gain = d_after - d_before  # positive is good

        # Main objective: after-move pursuit quality + avoid getting boxed in by opponent
        quality = chosen_val if chosen_val is not None else (0, 0, 0)
        val2 = (quality[0], quality[1], quality[2], opp_gain, -abs(nx - sx) - abs(ny - sy))

        if best_val is None or val2 > best_val:
            best_val = val2
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]