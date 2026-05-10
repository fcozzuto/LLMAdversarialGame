def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles", [])
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or (("evad" in opp_role) and ("evad" not in self_role))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obs_set

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx*dx + dy*dy  # squared

    # Goal heuristic
    if pursuer:
        gx, gy = ox, oy
    else:
        # Evader: maximize distance to pursuer by aiming at farthest corner (deterministic)
        best = None
        for cx, cy in corners:
            score = cheb(sx, sy, cx, cy) + 2*cheb(ox, oy, cx, cy)
            if best is None or score > best[0]:
                best = (score, cx, cy)
        gx, gy = best[1], best[2]

    # Choose best move by minimizing (pursuer) or maximizing (evader) next-state objective
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Encourage actual progress toward goal and slight cornering
        dist2 = cheb(nx, ny, gx, gy)
        toward_opp2 = cheb(nx, ny, ox, oy)
        val = toward_opp2 if pursuer else -toward_opp2
        val += -0.01*dist2 if pursuer else 0.01*dist2

        # Deterministic tie-break by fixed delta ordering preference: first in list wins
        if best_val is None or (pursuer and val < best_val) or ((not pursuer) and val > best_val):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]