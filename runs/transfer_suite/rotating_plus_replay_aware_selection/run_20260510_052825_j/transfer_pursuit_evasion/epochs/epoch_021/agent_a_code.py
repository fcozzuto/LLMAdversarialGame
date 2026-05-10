def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower().replace("-", "_")
    opponent_role = (observation.get("opponent_role") or "").lower().replace("-", "_")

    def is_ev(r):
        return ("evad" in r) or (r == "evader")
    def is_pu(r):
        return ("purs" in r) or (r == "pursuer")

    pursuer = True
    if is_pu(self_role) and not is_ev(self_role):
        pursuer = True
    elif is_pu(opponent_role) and not is_ev(opponent_role):
        pursuer = False

    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def dist2(x, y): 
        dx = x - ox; dy = y - oy
        return dx*dx + dy*dy

    best = None
    best_key = None
    for dx, dy in deltas:
        nx = sx + dx; ny = sy + dy
        if not free(nx, ny):
            continue
        d = dist2(nx, ny)
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center = -((nx - cx)*(nx - cx) + (ny - cy)*(ny - cy))
        # pursuer: minimize distance; evader: maximize distance. Deterministic tie-breaker uses center then dx,dy.
        key = (d if pursuer else -d, -center, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]