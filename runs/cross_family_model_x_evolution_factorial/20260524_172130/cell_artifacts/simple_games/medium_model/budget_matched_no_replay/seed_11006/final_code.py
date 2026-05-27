def choose_move(observation):
    # Minimal deterministic move: chase nearest resource if known, else approach opponent, else stay.
    grid_w = observation.get('grid_width', 0)
    grid_h = observation.get('grid_height', 0)
    sx, sy = observation.get('self_position', (0, 0))
    ox, oy = observation.get('opponent_position', (0, 0))
    resources = observation.get('resources', [])
    obstacles = observation.get('obstacles', [])
    # Default to stay
    dx = 0
    dy = 0

    def manhattan(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    # Try to move toward nearest resource
    if resources:
        best = None
        best_dist = None
        for r in resources:
            rx, ry = r[:2]
            dist = manhattan((sx, sy), (rx, ry))
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best = (rx, ry)
        if best is not None and best_dist is not None and best_dist != 0:
            rx, ry = best
            dx = 1 if rx > sx else -1 if rx < sx else 0
            dy = 1 if ry > sy else -1 if ry < sy else 0
            return [dx, dy]

    # If no resources, move toward opponent to contest
    if (ox, oy) != (sx, sy):
        dx = 1 if ox > sx else -1 if ox < sx else 0
        dy = 1 if oy > sy else -1 if oy < sy else 0
        return [dx, dy]

    # If same position (unlikely), stay
    return [0, 0]
