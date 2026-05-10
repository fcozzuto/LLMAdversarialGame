def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources_raw = observation.get("resources") or []
    resources = []
    for p in resources_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def next_pos(dx0, dy0):
        nx, ny = sx + dx0, sy + dy0
        if inb(nx, ny):
            return nx, ny
        return sx, sy

    if not resources:
        return [0, 0]

    # Pick nearest resource (deterministic tie-break by position order)
    best_t = resources[0]
    best_d = cheb(sx, sy, best_t[0], best_t[1])
    for tx, ty in resources[1:]:
        d = cheb(sx, sy, tx, ty)
        if d < best_d or (d == best_d and (tx, ty) < best_t):
            best_d = d
            best_t = (tx, ty)
    tx, ty = best_t

    cur_to_target = cheb(sx, sy, tx, ty)
    opp_to_target = cheb(ox, oy, tx, ty)
    adjacent_opp = cheb(sx, sy, ox, oy) <= 1

    best_move = (0, 0)
    best_val = None

    for dx0, dy0 in deltas:
        nx, ny = next_pos(dx0, dy0)
        if nx == ox and ny == oy:
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        opp_d = cheb(nx, ny, ox, oy)

        # Primary: get closer to target; Secondary: avoid opponent; Tertiary: prevent opponent getting ahead
        val = -d_to_target * 100
        if adjacent_opp:
            val += opp_d * 10
        else:
            val += opp_d
        opp_after = cheb(ox, oy, tx, ty)  # opponent stays in its own turn estimate; we just bias against losing the race
        if opp_to_target <= cur_to_target and opp_after <= d_to_target:
            val -= 50

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx0, dy0)

    return [int(best_move[0]), int(best_move[1])]