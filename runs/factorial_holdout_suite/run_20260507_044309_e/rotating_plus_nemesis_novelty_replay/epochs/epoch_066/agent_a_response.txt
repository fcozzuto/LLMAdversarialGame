def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we are ahead; if tied/behind, still choose ones we can overtake sooner.
        # Tie-break deterministically: larger (we can arrive sooner), then smaller ds, then lexicographic.
        candidates.append((do - ds, -(ds), rx, ry, ds, do))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    _, _, tx, ty, ds0, do0 = candidates[0]

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Score move by improving our distance; also avoid moves that give opponent an immediate advantage.
        my_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        opp_after = None
        # Approximate opponent reaction: if they are closer to target than we are after move, penalize.
        if do0 <= ds0:
            opp_after = 1
        else:
            opp_after = 0
        # Small deterministic nudge to reduce oscillations: prefer moves with smaller (dx,dy) ordering.
        key = (-(my_d), (do0 - my_d), -opp_after, -abs(tx - nx) - abs(ty - ny), -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    if best_key is None:
        return [0, 0]
    return best_move