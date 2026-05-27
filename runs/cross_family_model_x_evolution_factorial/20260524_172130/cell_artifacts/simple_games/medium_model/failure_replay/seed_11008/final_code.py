def choose_move(observation):
    # Defensive defaults
    dx = 0
    dy = 0

    # Safely access position
    pos = observation.get('position', {})
    x = pos.get('x', 0)
    y = pos.get('y', 0)

    # Try to bias towards center-ish area to stabilize plays across modes
    board = observation.get('board', {})
    h = board.get('height', 0)
    w = board.get('width', 0)

    if w > 0 and h > 0:
        cx = w // 2
        cy = h // 2
        dx_center = 1 if cx > x else -1 if cx < x else 0
        dy_center = 1 if cy > y else -1 if cy < y else 0
        dx = dx_center
        dy = dy_center

    if dx == 0 and dy == 0:
        # Try to move toward an available neighbor deterministically
        neighbors = observation.get('neighbors', [])
        if isinstance(neighbors, list) and len(neighbors) > 0:
            first = neighbors[0]
            dx = first.get('dx', 0)
            dy = first.get('dy', 0)
            if dx not in (-1, 0, 1):
                dx = 0
            if dy not in (-1, 0, 1):
                dy = 0

    # Final safety clamp
    if dx not in (-1, 0, 1):
        dx = 0
    if dy not in (-1, 0, 1):
        dy = 0

    return [dx, dy]
