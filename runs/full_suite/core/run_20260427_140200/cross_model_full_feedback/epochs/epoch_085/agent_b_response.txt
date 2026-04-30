def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def adjacent(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1])) == 1

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    center = (w // 2, h // 2)

    best = (0, 0)
    best_score = -10**9

    # Helper: distance to target
    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # If there are resources, prefer closest resource while avoiding obstacles and opposing proximity
    if resources:
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not in_bounds(nx, ny): 
                continue
            if (nx, ny) in obstacles:
                continue
            # distance to nearest resource after move
            new_pos = (nx, ny)
            dists = [man(new_pos, r) for r in resources]
            if not dists:
                continue
            dist_to_res = min(dists)
            # aggression: prefer being closer to resource and also reduce distance to opponent if possible
            dist_to_opp = man(new_pos, (ox, oy))
            score = -dist_to_res * 2 - dist_to_opp
            if score > best_score:
                best_score = score
                best = (dx, dy)
    else:
        # No resources: move toward center to balance position, but avoid obstacles and opponent
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            dist_to_center = man((nx, ny), center)
            dist_to_opp = man((nx, ny), (ox, oy))
            score = -dist_to_center - dist_to_opp
            if score > best_score:
                best_score = score
                best = (dx, dy)

    return [best[0], best[1]]