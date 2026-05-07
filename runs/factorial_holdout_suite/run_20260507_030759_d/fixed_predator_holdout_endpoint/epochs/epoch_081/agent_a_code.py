def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx = int(sp[0]) if len(sp) > 0 else 0
    sy = int(sp[1]) if len(sp) > 1 else 0
    ox = int(op[0]) if len(op) > 0 else w - 1
    oy = int(op[1]) if len(op) > 1 else h - 1

    def parse_cells(lst):
        out = []
        for p in lst or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x = int(p[0]); y = int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.append((x, y))
        return out

    obstacles = set(parse_cells(observation.get("obstacles")))
    resources = [c for c in parse_cells(observation.get("resources")) if c not in obstacles]

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    best = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer targets we can reach first; then closer; then deterministic tie-break by parity
        key = (od - sd, -sd, -((tx + ty) & 1), tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    vx = 1 if tx > sx else -1 if tx < sx else 0
    vy = 1 if ty > sy else -1 if ty < sy else 0

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cand = []
    if vx == 0 and vy == 0:
        return [0, 0]
    cand.append((vx, vy))
    if vx != 0: cand.append((vx, 0))
    if vy != 0: cand.append((0, vy))
    cand.append((0, 0))

    for dx, dy in cand:
        nx = sx + dx; ny = sy + dy
        if free(nx, ny) and dx in (-1, 0, 1) and dy in (-1, 0, 1):
            return [int(dx), int(dy)]

    return [0, 0]