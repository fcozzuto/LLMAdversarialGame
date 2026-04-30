def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    target = None
    best_adv = None
    for r in resources:
        r = tuple(r)
        ds = dist2((x, y), r)
        do = dist2((ox, oy), r)
        adv = ds - do  # negative means we are closer
        if target is None or adv < best_adv:
            best_adv = adv
            target = r

    if target is None:
        # No resources; simply move away from opponent if possible
        target = (0, 0)

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        to_t = dist2((nx, ny), target) if target != (0, 0) else 0
        to_o = dist2((nx, ny), (ox, oy))
        if resources and target != (0, 0):
            # small preference to move towards target and away from opponent
            score = (-to_t) + (0.03 * to_o)
        else:
            score = to_o  # maximize distance if no resources

        # contest bonus if target is a resource and we move closer than opponent this turn would
        if resources and target in resources:
            my_closer = dist2((nx, ny), target) <= dist2((ox, oy), target)
            if my_closer:
                score += 0.5

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]