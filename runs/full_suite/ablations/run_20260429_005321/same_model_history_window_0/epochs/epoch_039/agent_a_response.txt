def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    grid_w = observation.get("grid_width", 8)
    grid_h = observation.get("grid_height", 8)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource where we are relatively closer than opponent
    best = None
    best_score = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((x, y), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # prefer immediate reach, then relative advantage
        score = (do - ds) * 10 - ds
        if ds == 0:
            score += 10**6
        if score > best_score:
            best_score = score
            best = (rx, ry)

    # If no resources, drift away from opponent slightly
    if best is None:
        tx, ty = (ox, oy)
        dx = 1 if x <= tx else -1 if x > tx else 0
        dy = 1 if y <= ty else -1 if y > ty else 0
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_w and 0 <= ny < grid_h and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    rx, ry = best
    # Candidate moves (including stay)
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_w and 0 <= ny < grid_h and (nx, ny) not in obstacles:
                ns = dist((nx, ny), (rx, ry))
                # slight penalty if opponent also gets closer too
                no = dist((ox + (1 if ox < nx else -1 if ox > nx else 0), oy + (1 if oy < ny else -1 if oy > ny else 0)), (rx, ry))
                candidates.append((ns + 0.2 * no, dx, dy))

    # Deterministically choose best candidate
    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return [candidates[0][1], candidates[0][2]]