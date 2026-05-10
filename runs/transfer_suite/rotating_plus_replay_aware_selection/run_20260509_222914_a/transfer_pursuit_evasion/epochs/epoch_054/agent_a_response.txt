def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "pursuit"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obst_near_score(x, y):
        # More free space is better; deterministic by fixed weighting.
        md = 10
        for (bx, by) in obstacles:
            dx = abs(x - bx)
            dy = abs(y - by)
            m = dx if dx > dy else dy
            if m < md:
                md = m
        return md  # larger is better

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = max(abs(nx - ox), abs(ny - oy))  # capture proxy (radius 0)
        val = (d if is_pursuer else -d)
        # Prefer moves that stay away from obstacles (useful vs wall-run evasion).
        val += 0.08 * obst_near_score(nx, ny)
        # Slight preference to avoid standing still when chasing (helps escape loops).
        if is_pursuer and (dx == 0 and dy == 0):
            val -= 0.02
        if (not is_pursuer) and (dx == 0 and dy == 0):
            val += 0.01  # evader can "stall" safely sometimes
        # Deterministic tie-break via lexicographic move order
        if val > best_val:
            best_val = val
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]