def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (W - 1, H - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    un_cells = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in blocked:
                un_cells.append((x, y))

    def best_target():
        if not un_cells:
            return None
        cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
        best = None
        best_key = None
        for tx, ty in un_cells:
            d_us = dist(sx, sy, tx, ty)
            d_op = dist(ox, oy, tx, ty)
            key = (d_op - d_us, -d_us, - (abs(tx - cx) + abs(ty - cy)), tx, ty)
            if best_key is None or key > best_key:
                best_key, best = key, (tx, ty)
        return best

    t = best_target()

    def sign(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    def valid(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in blocked

    if t is None:
        for dx, dy in moves:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    tx, ty = t
    dx1, dy1 = sign(tx - sx), 0
    dx2, dy2 = 0, sign(ty - sy)

    cand = []
    if dx1 != 0 and valid(sx + dx1, sy + dy1):
        cand.append((dist(sx + dx1, sy, tx, ty), 0, dx1, 0))
    if dy2 != 0 and valid(sx + dx2, sy + dy2):
        cand.append((dist(sx, sy + dy2, tx, ty), 0, 0, dy2))

    # If direct moves are blocked or unhelpful, fall back deterministically
    if not cand:
        for dx, dy in moves:
            if valid(sx + dx, sy + dy):
                nx, ny = sx + dx, sy + dy
                # Prefer cells closer to target and farther from opponent
                key = (dist(nx, ny, tx, ty), -dist(nx, ny, ox, oy), dx, dy)
                cand = [key + (dx, dy)]
                break
        if not cand:
            return [0, 0]

    cand.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    _, _, dx, dy = cand[0]
    if valid(sx + dx, sy + dy):
        return [int(dx), int(dy)]

    for dx, dy in moves:
        if valid