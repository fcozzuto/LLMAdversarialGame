def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    inb = lambda nx, ny: 0 <= nx < w and 0 <= ny < h
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def neighbors_any(nx, ny, s):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    ax, ay = nx + dx, ny + dy
                    if (ax, ay) in s:
                        return True
        return False
    def nearest_to_set_dist(nx, ny, s):
        if not s:
            return 10**9
        md = 10**9
        for px, py in s:
            d = (px - nx) * (px - nx) + (py - ny) * (py - ny)
            if d < md:
                md = d
        return md
    # Determine high-level intention: if many unclaimed remain, expand; otherwise counter-attack.
    unclaimed_list = list(unclaimed)
    mode_attack = len(unclaimed_list) < 10 or len(opp) > 0
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        if (nx, ny) in opp:
            score += 2000  # flipping opponent cell on entry
        if (nx, ny) in unclaimed:
            score += 1200
        # Border pressure: move next to opponent territory / unclaimed.
        if neighbors_any(nx, ny, opp):
            score += 300 if mode_attack else 180
        if neighbors_any(nx, ny, unclaimed):
            score += 220
        # Distance shaping (favors frontier depending on mode).
        if mode_attack:
            score += -nearest_to_set_dist(nx, ny, opp) * 0.02
            score += -nearest_to_set_dist(nx, ny, set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))) * 0.005
        else:
            # Prefer moving toward large unclaimed clusters near opponent.
            score += -nearest_to_set_dist(nx, ny, unclaimed) * 0.03
            score += -nearest_to_set_dist(nx, ny, opp) * 0.01
        # Tiny tie-breaker: deterministic preference toward axes then diagonals.
        score += (0.001 if dx == 0 or dy == 0 else 0.0)
        if score > best[0]:
            best = (score, dx, dy)
    _, dx, dy = best
    return [int(dx), int(dy)]