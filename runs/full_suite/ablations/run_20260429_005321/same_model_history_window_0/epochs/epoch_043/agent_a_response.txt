def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy
    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    if not resources:
        # Move away from opponent if no resources visible
        best = (0, (0, 0))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            if d > best[0]:
                best = (d, (dx, dy))
        return list(best[1])
    # Pick best move by evaluating advantage on the best target resource
    best_score = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate against a single best resource for this move
        candidate_best = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Strongly prefer resources where we can arrive earlier (or block by being closer)
            adv = do - ds
            score = adv * 1000 - ds * 3
            # Mild tie-break: prefer closer resources when no advantage
            if adv <= 0:
                score -= (ds + cheb(ox, oy, rx, ry)) * 0.2
            # Prevent moving into "almost certain contest" where opponent is equally close
            if adv == 0:
                score -= 15
            if score > candidate_best:
                candidate_best = score
        # If currently already best, encourage staying if it's optimal
        if candidate_best > -10**8:
            if best_score is None or candidate_best > best_score:
                best_score = candidate_best
                best_move = (dx, dy)
            elif candidate_best == best_score:
                # Deterministic tie-break: prefer moves with larger dx, then dy, then keep still
                if (abs(dx), abs(dy), dx, dy) > (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1]):
                    best_move = (dx, dy)
    return [best_move[0], best_move[1]]