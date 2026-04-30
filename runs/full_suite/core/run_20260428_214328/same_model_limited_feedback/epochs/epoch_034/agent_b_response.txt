def choose_move(observation):
    W = observation.get('grid_width', 8)
    H = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def best_target(from_pos):
        if not resources:
            return (from_pos[0], from_pos[1])
        best = resources[0]
        bd = dist(from_pos, best)
        for r in resources[1:]:
            d = dist(from_pos, r)
            if d < bd:
                bd = d
                best = r
        return best

    self_t = best_target((sx, sy))
    opp_t = best_target((ox, oy))

    best_move = (0, 0)
    best_val = -10**18

    # Small preference to move "north/east" to break ties consistently
    tie_bias = {(-1,-1):0,(0,-1):1,(1,-1):2,(-1,0):3,(0,0):4,(1,0):5,(-1,1):6,(0,1):7,(1,1):8}

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H:
            continue
        if (nx, ny) in obstacles:
            continue

        newpos = (nx, ny)
        val = 0

        # If we stand on a resource, take it decisively
        if newpos in set(tuple(r) for r in resources):
            val += 10000

        # Primary: get closer to our target
        val += -dist(newpos, self_t) * 10

        # Secondary: deny opponent by moving toward their target
        # (encourage getting closer to opponent's target while not wandering far)
        val += (dist((ox, oy), opp_t) - dist(newpos, opp_t)) * 6

        # Avoid getting too close to obstacles is not directly possible without local map info;
        # instead discourage moving to squares adjacent to many obstacles.
        adj = 0
        for ex, ey in obstacles:
            if dist(newpos, (ex, ey)) == 0:
                adj += 3
            elif dist(newpos, (ex, ey)) == 1:
                adj += 1
        val -= adj * 2

        # Deterministic tie-breaking
        val = val * 100 + (10 - tie_bias[(dx, dy)])

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]