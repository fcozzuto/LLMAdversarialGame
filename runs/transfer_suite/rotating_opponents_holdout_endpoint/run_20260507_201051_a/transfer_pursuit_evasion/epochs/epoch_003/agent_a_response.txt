def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    self_role = (observation.get("self_role", "") or "").lower()
    obstacles = observation.get("obstacles", []) or []

    sx, sy = int(self_pos[0]), int(self_pos[1])
    px, py = int(opp_pos[0]), int(opp_pos[1])
    ox = { (int(o[0]), int(o[1])) for o in obstacles }

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    is_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("hunter" in self_role) or ("pursuer" in self_role)
    # If role is unclear, assume pursuer when score favors capture mechanics.
    if self_role == "":
        is_pursuer = True

    best = None
    best_val = None
    eps = 0  # deterministic tie-break via move order only

    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)
        if (nx, ny) in ox:
            continue

        dist = cheb(nx, ny, px, py)
        # Obstacle safety: prefer moves that increase clearance from nearest obstacle.
        clearance = 0
        if ox:
            md = 10**9
            for (oxx, oyy) in ox:
                d2 = cheb(nx, ny, oxx, oyy)
                if d2 < md: md = d2
            clearance = md

        # If pursuer: minimize dist; if evader: maximize dist.
        primary = dist if is_pursuer else -dist
        # Obstacle-aware tie-break: pursuer prefers slightly larger clearance too (avoid being trapped).
        secondary = -clearance if is_pursuer else clearance

        val = (primary, secondary, eps + i)
        if best is None or val < best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]