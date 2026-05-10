def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    opp_is_evader = ("evader" in opp_role) or ("escape" in opp_role) or ("runner" in opp_role)
    if self_is_evader == opp_is_evader:
        # Default assumption: one is pursuer, other evader.
        self_is_evader = False

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_score(nx, ny):
        # Hard avoid obstacles (engine would reject by staying, but score must avoid bad moves)
        if (nx, ny) in obs:
            return -10**9
        # Distance to opponent
        d_opp = abs(nx - ox) + abs(ny - oy)
        # Prefer moving away/towards depending on role
        base = d_opp if self_is_evader else -d_opp
        # Repel from obstacles
        # (use Chebyshev-ish local penalty with small radius)
        pen_obs = 0
        for oxp, oyp in obs:
            man = abs(nx - oxp) + abs(ny - oyp)
            if man == 0:
                pen_obs += 100
            elif man == 1:
                pen_obs += 5
            elif man == 2:
                pen_obs += 2
        # Slight preference for having more free adjacent space
        free = 0
        for dx, dy in deltas:
            tx, ty = nx + dx, ny + dy
            if in_bounds(tx, ty) and (tx, ty) not in obs:
                free += 1
        # Corner bias for deterministic stable behavior
        corner_bias = -((nx - (0 if nx <= w//2 else w-1))**2 + (ny - (0 if ny <= h//2 else h-1))**2) * 1e-6
        return base - pen_obs + free * (0.05 if not self_is_evader else 0.03) + corner_bias

    best_dx, best_dy = 0, 0
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        v = step_score(nx, ny)
        if best_val is None or v > best_val:
            best_val = v
            best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]