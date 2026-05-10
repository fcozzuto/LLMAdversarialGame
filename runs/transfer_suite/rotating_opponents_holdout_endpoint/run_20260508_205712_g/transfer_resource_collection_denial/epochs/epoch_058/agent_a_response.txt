def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(x), int(y)) for x, y in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_target(myx, myy):
        if not resources:
            tx = 0 if ox >= W // 2 else W - 1
            ty = 0 if oy >= H // 2 else H - 1
            return tx, ty
        best = None
        best_key = None
        for rx, ry in resources:
            d_my = man(myx, myy, rx, ry)
            d_op = man(ox, oy, rx, ry)
            # prefer targets we are closer to; if tie, prefer farther from opponent
            lead = d_op - d_my
            key = (-lead, d_my, d_op, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    def move_toward(target_x, target_y, cx, cy):
        bx, by = cx, cy
        best = None
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = man(nx, ny, target_x, target_y)
            if best is None or d < best[0] or (d == best[0] and (nx, ny) < best[1]):
                best = (d, (nx, ny))
        if best is None:
            return (0, 0)
        return (best[1][0] - cx, best[1][1] - cy)

    tx, ty = best_target(sx, sy)
    dx, dy = move_toward(tx, ty, sx, sy)
    nx, ny = sx + dx, sy + dy
    if (nx, ny) == (sx, sy):
        # If stuck, try a fallback target that is reachable by any legal move.
        best = None
        for r in resources[:]:
            rx, ry = r
            for mdx, mdy in moves:
                px, py = sx + mdx, sy + mdy
                if not inb(px, py) or (px, py) in obs:
                    continue
                d_my = man(px, py, rx, ry)
                d_op = man(ox, oy, rx, ry)
                lead = d_op - d_my
                key = (-lead, d_my, abs(px - rx) + abs(py - ry), px, py, rx, ry)
                if best is None or key < best[0]:
                    best = (key, (mdx, mdy))
        if best is not None:
            return [int(best[1][0]), int(best[1][1])]
        return [0, 0]
    return [int(dx), int(dy)]