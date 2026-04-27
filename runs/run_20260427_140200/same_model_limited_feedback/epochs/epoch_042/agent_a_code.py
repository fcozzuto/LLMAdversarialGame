def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for 8-neigh
    def valid(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h: 
            return False
        return (nx, ny) not in obstacles

    if not resources:
        # move away from opponent deterministically
        dx = -1 if ox > sx else (1 if ox < sx else 0)
        dy = -1 if oy > sy else (1 if oy < sy else 0)
        return [dx, dy]

    best_t = None
    best_gain = -10**9
    # Choose a resource where we have a clear distance advantage over opponent
    for r in resources:
        r = (r[0], r[1])
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        gain = od - sd
        # Slight tie-break to prefer closer overall
        score = gain*1000 - sd
        if score > best_gain:
            best_gain = score
            best_t = r

    tx, ty = best_t
    # If we cannot reach due to local block, move toward the least-blocked direction
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Greedy toward target
        d_to_t = dist((nx, ny), (tx, ty))
        # Repel from obstacles slightly: count adjacent blocked cells
        adj_block = 0
        for ax, ay in dirs:
            px, py = nx + ax, ny + ay
            if (px, py) in obstacles:
                adj_block += 1
        # Consider opponent: prefer moves that increase separation when we are not targeting strictly
        sep = dist((nx, ny), (ox, oy))
        # Deterministic weighting
        val = (-d_to_t*10) + (sep) - (adj_block*2)
        candidates.append((val, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [candidates[0][1], candidates[0][2]]