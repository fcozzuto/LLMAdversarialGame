def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    # Pick resource where we are relatively closer than opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        rel = ds - do
        key = (rel, ds, abs(rx - x) + abs(ry - y), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Candidate deltas, deterministic priority.
    deltas = [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]
    # Prefer moves that reduce distance to target; avoid obstacles and out of bounds.
    best_delta = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        cur = cheb(x, y, tx, ty)
        nd = cheb(nx, ny, tx, ty)
        # Encourage approach; slight tie-breakers to reduce movement and avoid moving away.
        score = (nd, nd - cur, abs(dx) + abs(dy), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_delta = [dx, dy]

    return best_delta