def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def king(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) >= abs(dy) else abs(dy)

    # Pick best resource by "arrive first" margin (opponent distance minus self distance).
    best = None
    for rx, ry in resources:
        ds = king(sx, sy, rx, ry)
        do = king(ox, oy, rx, ry)
        margin = do - ds
        # Tie-break: prefer smaller self distance, then prefer resources more "towards center".
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center_bias = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))
        score = (margin, -ds, center_bias)
        if best is None or score > best[0]:
            best = (score, (rx, ry))
    _, (tx, ty) = best

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                ds2 = king(nx, ny, tx, ty)
                # If we step onto a cell that is closer to the target than staying, reward.
                stay_ds = king(sx, sy, tx, ty)
                improve = stay_ds - ds2
                # Light contention term: prefer states where opponent is relatively farther.
                do = king(ox, oy, tx, ty)
                score = (improve, (do - ds2), -ds2, -abs(nx - tx) - abs(ny - ty))
                candidates.append((score, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0], reverse=True)
    return candidates[0][1]