def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    ti = int(observation.get("turn_index", 0) or 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        for (tx, ty) in resources:
            ds = manh(sx, sy, tx, ty)
            do = manh(ox, oy, tx, ty)
            if best is None:
                best = (tx, ty, ds, do)
            else:
                # Prefer resources we can reach earlier; penalize those opponent can reach soon.
                # Deterministic tie-break using coordinates and turn index.
                cur = best
                cur_tx, cur_ty, cur_ds, cur_do = cur
                key_best = (cur_ds - cur_do, cur_ds, -cur_do, cur_tx, cur_ty)
                key_new = (ds - do, ds, -do, tx, ty)
                # smaller is better for first three; then lexicographic
                if key_new < key_best:
                    best = (tx, ty, ds, do)
        tx, ty = best[0], best[1]
    else:
        # No visible resources: drift toward opponent-opposite corner to likely find new spawns.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # Choose corner farthest from opponent deterministically.
        tx, ty = max(corners, key=lambda c: (manh(c[0], c[1], ox, oy), -c[0], -c[1], ti % 3))[0], max(corners, key=lambda c: (manh(c[0], c[1], ox, oy), -c[0], -c[1], ti % 3))[1]

    # Greedy best next move toward target with light anti-denial: prefer reducing distance gap (us vs opp).
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ds2 = manh(nx, ny, tx, ty)
        do2 = manh(ox, oy, tx, ty)
        gap = ds2 - do2  # smaller => we are closer than opponent
        # Also ensure we actually move toward target (avoid too much staying when not needed)
        score = (gap, ds2, abs(nx - ox) + abs(ny - oy), (nx - sx) * (ny - sy), tx, ty)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]