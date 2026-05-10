def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    turns_remaining = int(observation.get("turns_remaining", 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (cd(c[0], c[1], ox, oy), -c[0], -c[1]))
        best = (-10**9, (0, 0))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = -cd(nx, ny, tx, ty) + 0.01 * cd(nx, ny, ox, oy)
            if score > best[0]:
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    # Choose a contested target: maximize (opp_dist - self_dist), then prefer closer to self.
    # Slightly favor keeping options early by using remaining turns.
    best_target = None
    best_key = (-10**18, -10**18)
    for rx, ry in resources:
        sd = cd(sx, sy, rx, ry)
        od = cd(ox, oy, rx, ry)
        margin = od - sd
        early = 0 if turns_remaining <= 0 else min(2.0, turns_remaining / 20.0)
        key = (margin * 10.0 + early * (od - sd) + (0.001 * (rx + 7 * ry)), -sd)
        if key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    # Pick move that most improves being first for target; tie-break by safety and resource proximity.
    best = (-10**18, (0, 0))
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = cd(nx, ny, tx, ty)
        nod = cd(ox, oy, tx, ty)  # opponent position unchanged this turn
        # Prefer capturing target sooner; if tied, prefer decreasing opponent's advantage.
        score = (nod - nsd) * 100.0 - nsd
        # Mild obstacle/safety: prefer moves that keep more in-bounds directions.
        safe_dirs = 0
        for adx, ady in deltas:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay):
                safe_dirs += 1
        score += 0.05 * safe_dirs
        # Deterministic tie-break
        score += 0.000001 * (nx * 8 + ny)
        if score > best[0]:
            best = (score, (dx, dy))
    return [best[1][0], best[1][1]]