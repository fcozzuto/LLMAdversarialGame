def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    # Choose a target resource where we have a distance advantage; otherwise nearest.
    def dist(a, b):  # Chebyshev for diagonal allowance
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    best_t = None
    best_val = -10**9
    for rx, ry in resources:
        d_s = dist((sx, sy), (rx, ry))
        d_o = dist((ox, oy), (rx, ry))
        # If we're closer, value increases sharply; also prefer fewer absolute steps.
        val = (d_o - d_s) * 10 - d_s
        if val > best_val:
            best_val = val
            best_t = (rx, ry)
    if best_t is None:
        best_t = (sx, sy)
    tx, ty = best_t
    # Evaluate possible moves deterministically.
    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    # If target is current tile, just run away from opponent a bit.
    target_same = (sx == tx and sy == ty)
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Scoring: move toward target; if tied/away, adjust to avoid opponent interference.
        d_t = dist((nx, ny), (tx, ty))
        d_o = dist((nx, ny), (ox, oy))
        # Prefer getting on target quickly; prefer increasing opponent distance.
        if target_same:
            score = d_o * 3
        else:
            score = -d_t * 10 + d_o * 2
        # Small tie-breaker: prefer moves that change position if equally good.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]