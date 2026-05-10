def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    res = {(p[0], p[1]) for p in resources}
    obs = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # Immediate pickup
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res and (nx, ny) not in obs:
            return [dx, dy]

    best = None  # (opp_d-self_d, -self_d, -(rx+ry), rx, ry)
    for rx, ry in res:
        if (rx, ry) in obs:
            continue
        sd = dist8(sx, sy, rx, ry)
        od = dist8(ox, oy, rx, ry)
        cand = (od - sd, -sd, -(rx + 2 * ry), rx, ry)
        if best is None or cand > best:
            best = cand
    _, _, _, tx, ty = best

    curd = dist8(sx, sy, tx, ty)
    best_m = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        nd = dist8(nx, ny, tx, ty)
        on_resource = 1 if (nx, ny) in res else 0
        # Prefer moves that progress toward the target and (secondarily) deny opponent advantage
        opp_now = dist8(ox, oy, tx, ty)
        opp_after = opp_now  # opponent doesn't move this turn in our decision
        cand = (on_resource, curd - nd, -(nd), (opp_after - nd), -abs(nx - tx) - abs(ny - ty))
        if best_m is None or cand > best_m:
            best_m = cand
            best_move = [dx, dy]
    return best_move