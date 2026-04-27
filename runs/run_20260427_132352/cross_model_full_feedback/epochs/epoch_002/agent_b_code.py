def choose_move(observation):
    # Deterministic 8x8 grid agent with simple heuristics
    turn_index = observation.get('turn_index', 0)
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    self_pos = observation.get('self_position', [0, 0])
    opp_pos = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    remaining = observation.get('remaining_resource_count', len(resources))

    sx, sy = self_pos
    ox, oy = opp_pos

    # Moves: 8 directions + stay
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles or (x == ox and y == oy)

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # If there are resources, target the closest one
    target = None
    best_r_score = None
    if resources:
        for r in resources:
            rx, ry = r
            d_self = dist((sx, sy), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            # Heuristic: prefer resources closer to us and farther from opponent
            score = (d_opp - d_self, -d_self, -(rx + ry*0))
            if best_r_score is None or score > best_r_score:
                best_r_score = score
                target = (rx, ry)
        tx, ty = target
    else:
        # No resources: move toward a stable retreat point (diagonal toward corner far from opponent)
        tx = 0 if ox > sx else w-1
        ty = 0 if oy > sy else h-1

    best_dx, best_dy = 0, 0
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if blocked(nx, ny) and not (nx == sx and ny == sy):
            continue
        # Prefer moving toward target
        d_to_t = dist((nx, ny), (tx, ty))
        d_to_opp = dist((nx, ny), (ox, oy))
        # Score: closer to target, farther from opponent, avoid getting too close to obstacle
        score = -d_to_t * 2 + d_to_opp
        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]