def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_set = set(tuple(r) for r in resources)

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Immediate capture if safe
    best_cap = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in res_set and (nx, ny) not in obstacles:
            if best_cap is None or dist2(nx, ny, ox, oy) < best_cap[0]:
                best_cap = (dist2(nx, ny, ox, oy), dx, dy)
    if best_cap:
        return [best_cap[1], best_cap[2]]

    # Resource race: prioritize resources we can reach earlier, while keeping opponent delay high
    best_score = None
    best_target = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist2(sx, sy, rx, ry)
        od = dist2(ox, oy, rx, ry)
        # Higher score is better: larger (od-sd) means opponent farther than us; break ties by closeness
        score = (od - sd) * 1000 - sd
        if best_score is None or score > best_score:
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target

    # Move one step greedily toward target, but discourage stepping near opponent if it harms capture potential
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer decreasing distance to target; if tie, prefer being farther from opponent to reduce denial impact
        d_to = dist2(nx, ny, tx, ty)
        d_from_opp = dist2(nx, ny, ox, oy)
        val = -d_to * 10 + d_from_opp * 0.01
        # Add small bonus if next cell is a resource (capture-thresholding)
        if (nx, ny) in res_set:
            val += 1e6
        if best_move is None or val > best_move[0]:
            best_move = (val, dx, dy)

    if best_move:
        return [best_move[1], best_move[2]]

    return [0, 0]