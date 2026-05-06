def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return (x, y) not in obstacles
    def dist2(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx * dx + dy * dy
    def edge(x, y):
        return x == 0 or x == w - 1 or y == 0 or y == h - 1

    if not resources:
        return [0, 0]

    opp_on_edge = edge(ox, oy)
    # If opponent patrols edges, go for resources on the opposite side to force distance-based races.
    if opp_on_edge:
        best_r = None
        best_key = None
        for rx, ry in resources:
            # opposite-side emphasis: maximize distance from opponent and prefer resources on far edge line
            farx = (w - 1 - rx) if ox < (w - 1) / 2 else rx
            fary = (h - 1 - ry) if oy < (h - 1) / 2 else ry
            key = (-(dist2(ox, oy, rx, ry)), -(farx + fary), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        # Otherwise, greedily pursue the closest resource.
        tx, ty = min(resources, key=lambda p: (dist2(sx, sy, p[0], p[1]), p[0], p[1]))

    # Choose move that best advances to target while discouraging opponent convergence.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not ok(nx, ny):
            continue
        my = dist2(nx, ny, tx, ty)
        opp = dist2(nx, ny, ox, oy)
        # Encourage staying farther from opponent while approaching target; keep deterministic tie-break.
        score_key = (my, -opp, dx, dy)
        if best is None or score_key < best[0]:
            best = (score_key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]