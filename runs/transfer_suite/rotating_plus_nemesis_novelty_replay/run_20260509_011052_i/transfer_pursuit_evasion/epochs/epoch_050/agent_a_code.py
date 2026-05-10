def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def next_cells():
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                yield dx, dy, nx, ny

    # Target choice for evader: farthest corner from opponent
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    tx, ty = (ox, oy) if pursuer else far_corner

    # Scoring: move closer (pursuer) or farther (evader) to target, plus tie-break for keeping away from opponent
    best = None
    best_score = None
    for dx, dy, nx, ny in next_cells():
        to_target = cheb(nx, ny, tx, ty)
        to_op = cheb(nx, ny, ox, oy)
        # Prefer approach/escape while also optimizing distance to opponent directly
        score = (to_target, to_op)
        if pursuer:
            key = (to_target, -to_op)  # closer to opponent/target, and farther from opponent if possible in ties
            better = (best_score is None) or (key < best_score)
        else:
            key = (-to_target, to_op)  # farther from target and farther from opponent
            better = (best_score is None) or (key < best_score)
        if better:
            best_score = key
            best = [dx, dy]

    # Fallback: stay if somehow all invalid (shouldn't happen)
    return best if best is not None else [0, 0]