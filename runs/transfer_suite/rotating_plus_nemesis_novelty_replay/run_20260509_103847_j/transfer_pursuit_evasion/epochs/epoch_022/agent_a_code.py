def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    role = observation.get("self_role", "pursuer")
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            if free(x + dx, y + dy):
                m += 1
        return m

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        # obstacle/wall-aware: avoid moving into tight spots while pursuing/escaping
        tight = -2.0 if mob <= 2 else (-1.0 if mob == 3 else 0.0)

        # If adjacent, prefer exact position (capture) deterministically.
        cap = 1000.0 if (nx == ox and ny == oy) else 0.0

        # Pursuer: minimize distance, reduce opponent escape space.
        # Evader: maximize distance, increase own escape space.
        if role == "pursuer":
            score = cap + (-d) + 0.35 * mob + tight
            # small bias toward blocking: prefer moves that reduce opponent mobility if they tried to go where we go
            score += -0.05 * mobility(ox, oy)
        else:
            score = cap + d + 0.35 * mob + tight

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best

    # Fallback: deterministic minimal-distance move ignoring obstacles (engine will clamp to stay if invalid).
    best = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        score = -d if role == "pursuer" else d
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]