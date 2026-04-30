def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, dict):
            if "pos" in r and r["pos"] is not None and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

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

    # Target selection: maximize "pressure" (we prefer resources opponent is far from), but
    # also avoid walking away from nearer resources by including self proximity.
    best_t = resources[0]
    best_v = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Larger is better; deterministic tie-break on position.
        v = (do - ds) * 10 - ds
        if best_v is None or v > best_v or (v == best_v and (rx, ry) < best_t):
            best_v = v
            best_t = (rx, ry)
    tx, ty = best_t

    # Move choice: consider all deltas, avoid obstacles, and score by
    # (decrease distance to target) and (increase distance from opponent).
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = moves[4]
    best_s = None
    cur_ds = cheb(sx, sy, tx, ty)
    cur_do = cheb(ox, oy, sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, nx, ny)
        # Prefer closer to target; also avoid opponent getting closer.
        s = (cur_ds - ds) * 100 + (do - cur_do) * 10 - ds
        if best_s is None or s > best_s or (s == best_s and (dx, dy) < best_m):
            best_s = s
            best_m = (dx, dy)

    # If all adjacent cells are invalid (blocked), stay.
    return [int(best_m[0]), int(best_m[1])]