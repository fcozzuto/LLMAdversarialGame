def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def target_key(rx, ry):
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        return (od - sd, -sd, -((rx * 131 + ry * 313) & 1023), rx, ry)

    resources_sorted = sorted(resources, key=lambda p: target_key(p[0], p[1]), reverse=True)
    tx, ty = resources_sorted[0]

    moves_all = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    start_shift = observation.get("turn_index", 0) % len(moves_all)
    moves = moves_all[start_shift:] + moves_all[:start_shift]

    best_move = (0, 0)
    best_val = None
    base_od = md(ox, oy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = md(nx, ny, tx, ty)
        # maximize our progress while keeping pressure on the opponent
        val = (base_od - myd, -myd, -(abs(ox - nx) + abs(oy - ny)), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]