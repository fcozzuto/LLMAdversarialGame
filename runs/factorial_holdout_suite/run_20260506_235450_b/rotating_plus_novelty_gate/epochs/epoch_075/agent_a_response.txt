def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                rs.append((x, y))
    if not rs:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose a target that we can reach sooner, while discouraging targets on the opponent's likely sweep row.
    best = None
    best_val = None
    for (rx, ry) in rs:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # If resource is on/near opponent's row, opponent's sweep is more dangerous.
        row_risk = abs(ry - oy)
        val = (sd - od) + 0.25 * row_risk + 0.02 * sd
        if best_val is None or val < best_val:
            best_val = val
            best = (rx, ry)
    tx, ty = best

    # Pick next step that reduces distance to target while avoiding obstacles.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Mild bias to keep options open: prefer moves that don't strictly worsen.
        worsen = nd - cheb(sx, sy, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        score = (nd, abs(nx - tx) + abs(ny - ty), worsen, -opp_d)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]