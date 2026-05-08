def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    self_role = (observation.get("self_role", "") or "").lower()

    obs_set = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obs_set.add((int(o[0]), int(o[1])))

    cap_r = int(observation.get("capture_radius", 0))  # not used directly, capture_radius=0
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs_set

    is_pursuer = ("pursuer" in self_role) or ("catch" in self_role) or ("chaser" in self_role) or ("pursuit" in self_role)

    # Deterministic objective: pursuer minimizes dist; evader maximizes dist.
    # Also lightly penalize moves that step adjacent to obstacles to avoid getting boxed in.
    adj_pen = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if False:
                adj_pen += 1  # keep deterministic structure; adj_pen unused

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # For evader, bias toward the corner farthest from pursuer (with a tiny turn-based tie-break).
    far_corner = corners[0]
    best_corner_score = -1
    for cx, cy in corners:
        s = d2(cx, cy, ox, oy)
        if s > best_corner_score:
            best_corner_score = s
            far_corner = (cx, cy)

    best = None
    best_score = None
    tx, ty = far_corner

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist = d2(nx, ny, ox, oy)
        # obstacle proximity penalty (0 if no nearby obstacle)
        prox = 0
        for ax, ay in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            if (nx + ax, ny + ay) in obs_set:
                prox += 1

        if is_pursuer:
            # chase while steering away from obstacles slightly
            score = dist + 2 * prox
            better = (best_score is None) or (score < best_score) or (score == best_score and (dx, dy) < best)
        else:
            # evade: maximize distance, also head to far corner deterministically
            corner_dist = d2(nx, ny, tx, ty)
            # tie-break using turn_index to avoid repeating exact loop when equal
            t = int(observation.get("turn_index", 0))
            score = -(dist + 0.15 * corner_dist) + 2 * prox + (0.001 * ((t + dx + 2 * dy) % 7))
            better = (best_score is None) or (score < best_score) or (score == best_score and (dx, dy) < best)

        if better:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]