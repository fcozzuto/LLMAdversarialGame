def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Opponent's likely target: closest resource to opponent
    tx, ty = min(resources, key=lambda r: md(ox, oy, r[0], r[1]))
    opp_to_t = md(ox, oy, tx, ty)

    best_key = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue

        our_to_t = md(nx, ny, tx, ty)

        # Secondary objective: move toward our closest resource
        our_nearest = 10**9
        for rx, ry in resources:
            d = md(nx, ny, rx, ry)
            if d < our_nearest:
                our_nearest = d

        # Primary: intercept/deny by getting as close or closer than opponent to their target
        # Key: prefer smaller (our_to_t - opp_to_t); then smaller our_nearest; then deterministic move order
        key = (our_to_t - opp_to_t, our_nearest, moves.index((dx, dy)))
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move