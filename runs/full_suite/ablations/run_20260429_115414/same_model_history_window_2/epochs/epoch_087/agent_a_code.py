def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_step_toward(tx, ty, prefer_block_avoid=True):
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                d1 = cheb(nx, ny, tx, ty)
                d0 = cheb(nx, ny, ox, oy)
                # Prefer moves that keep opponent far and progress toward target.
                score = d1 * 3 + d0 * 1
                if prefer_block_avoid:
                    # Small penalty if move increases distance to board center (avoid corner trapping).
                    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                    score += 0.05 * (cheb(nx, ny, cx, cy))
                if best is None or score < best[0]:
                    best = (score, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]

    if resources:
        # Materially different: pick target that maximizes "control" gap (opponent farther than us),
        # with deterministic tie-breaking by closer-to-us.
        best = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            control = d_op - d_me
            # If control ties, prefer lower d_me; if still ties, prefer lexicographically smaller (rx,ry).
            key = (-control, d_me, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

        # If standing on target (or adjacent), still move so we don't get stuck on obstacles.
        return best_step_toward(tx, ty)
    else:
        # No resources: go toward the nearest side (center-ish) deterministically while staying safe.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        return best_step_toward(cx, cy, prefer_block_avoid=True)