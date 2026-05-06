def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target(tx, ty):
        # key: maximize (opp_dist - self_dist), then prefer closer self, then deterministic coord
        best = None
        best_key = None
        for cx, cy in resources:
            sd = cheb(tx, ty, cx, cy)
            od = cheb(ox, oy, cx, cy)
            key = (od - sd, -sd, cx, cy)
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best, best_key

    if not resources:
        return [0, 0]

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If stuck, allow staying; otherwise avoid obstacle collisions when possible.
    best_move = [0, 0]
    best_score = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        _, key = best_target(nx, ny)
        if key is None:
            continue
        # tie-break prefers moves that keep/advance advantage, then move closer
        adv, neg_sd, cx, cy = key
        sd = -neg_sd
        # secondary: slightly prefer moving toward the chosen target direction
        step_to_target = 0
        if cx != nx:
            step_to_target += 1 if (cx > nx and dx > 0) or (cx < nx and dx < 0) else 0
        if cy != ny:
            step_to_target += 1 if (cy > ny and dy > 0) or (cy < ny and dy < 0) else 0
        score = (adv, -sd, step_to_target, cx, cy, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all candidate moves were invalid (rare), deterministic fallback: stay.
    return best_move