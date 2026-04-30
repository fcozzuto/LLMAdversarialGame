def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    rem = observation.get("remaining_resource_count", len(resources))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # If we're on a resource, prefer staying to secure? but still allow move.
    if resources:
        nearest = min(resources, key=lambda r: (sx - r[0])**2 + (sy - r[1])**2)
        tx, ty = nearest
    else:
        tx, ty = ox, oy

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = clamp(sx + dx, 0, w-1), clamp(sy + dy, 0, h-1)
        if (nx, ny) in obstacles:
            continue
        # Distance to nearest resource (after move)
        if resources:
            dres = min((nx-r[0])**2 + (ny-r[1])**2 for r in resources)
        else:
            dres = 0
        # Distance to opponent (small deterrence / blocking)
        dop = (nx-ox)**2 + (ny-oy)**2
        # Encourage moves that approach resources; discourage proximity to opponent when close
        score = -dres
        if rem <= 4:
            # Late game: try to control by getting closer to opponent and resources
            score += (1.0 / (dop + 1)) * 20.0
        else:
            # Early/mid: avoid getting too close to opponent while still pursuing
            if dop < 9:
                score -= (9 - dop) * 2.0
        # Prefer taking a resource cell if present
        if (nx, ny) in set(tuple(r) for r in resources):
            score += 1e6
        # Tie-break deterministically by keeping order already; use score only
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best