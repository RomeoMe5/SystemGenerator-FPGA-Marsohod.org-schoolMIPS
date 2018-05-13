import sys

from rq import get_current_job

import engine.boards
from web_client import create_app, db

app = create_app()
app.app_context().push()


def _set_task_progress(progress: float or int) -> None:
    """ Updates task progress throw setting it's meta property. """
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress', {
            'task_id': job.get_id(),
            'progress': progress
        })
        if progress >= 100:
            task.complete = True
        db.session.commit()


def generate_config(project_name: str, board: str, **params) -> None:
    try:
        _set_task_progress(0)
        # dynamicaly get target board
        board = getattr(engine.boards, board).archive(project_name, **params)
        _set_task_progress(100)
    except BaseException:
        _set_task_progress(100)
        app.logger.error("Unhandled exception", exc_info=sys.exc_info())
