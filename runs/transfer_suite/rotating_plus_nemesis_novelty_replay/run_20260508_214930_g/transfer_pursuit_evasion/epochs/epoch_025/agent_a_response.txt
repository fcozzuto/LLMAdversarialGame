def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy
    def free_neighbors(x, y):
        cnt = 0
        for dx, dy in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)):
            nx, ny = x + dx, y + dy
            if valid(nx, ny): cnt += 1
        return cnt

    is_pursuer = ("pursuer" in self_role) or ("pursue" in self_role)
    if not is_pursuer and ("pursuer" in opponent_role):
        is_pursuer = False
    elif not is_pursuer:
        # If roles are not explicit, assume pursuit in pursuit_evasion.
        is_pursuer = True

    deltas = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1,-1), (-1,1), (1,-1), (1,1)]
    best_move = [0, 0]
    best_key = None

    target_sign = -1 if is_pursuer else 1  # pursuer minimizes, evader maximizes
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        d = dist2(nx, ny, ox, oy)
        # Encourage obstacle avoidance + progress: score is oriented so bigger is better.
        # For pursuer: higher -d (i.e., smaller d) and more neighbor freedom.
        # For evader: higher +d and more neighbor freedom.
        progress = -d if is_pursuer else d
        neigh = free_neighbors(nx, ny)
        # Tie-break: prefer reducing/keeping Chebyshev distance when pursuing; opposite when evading.
        cheb = max(abs(nx - ox), abs(ny - oy))
        tie = -cheb if is_pursuer else cheb
        key = (progress * 1000 + neigh, tie, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move