def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = [(p[0], p[1]) for p in observation["resources"]]
    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy
    def best_target():
        if not resources:
            return None
        best = None
        best_gain = -10**9
        for r in resources:
            sg = dist((sx, sy), r)
            og = dist((ox, oy), r)
            gain = og - sg  # positive: we're closer
            # prefer closer when tie, and higher opponent disadvantage
            if gain > best_gain or (gain == best_gain and sg < dist((sx, sy), best)):
                best_gain = gain
                best = r
        return best
    target = best_target()
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if target is None:
        tx, ty = (w // 2, h // 2)
        options = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                options.append((dist((nx, ny), (tx, ty)), dx, dy))
        if not options:
            return [0, 0]
        options.sort()
        return [options[0][1], options[0][2]]
    best_score = -10**18
    best_move = (0, 0)
    opp_dist_now = dist((ox, oy), target)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_self_next = dist((nx, ny), target)
        # Primary: minimize distance to target; Secondary: maximize advantage over opponent
        # Capture reward if stepping onto resource
        cap = 0
        if (nx, ny) == target:
            cap = 1000000 - d_self_next
        score = -d_self_next + cap + (opp_dist_now - dist((ox, oy), target)) * 0.0
        # Advantage term: if opponent is closer to this target, penalize
        score += (opp_dist_now - d_self_next) * 0.5
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]